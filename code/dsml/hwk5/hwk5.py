from multiprocessing import Value
from matplotlib.pyplot import plot
import numpy as np
import math
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split


def sgd(
    gradient,
    gradient_js,
    x,
    y,
    start,
    ideal,
    learn_rate=0.1,
    batch_size=1,
    n_iter=50,
    tolerance=1e-06,
    dtype="float64",
    random_state=None,
    plot_title="",
    mul=1,
    filename="",
):
    # Checking if the gradient is callable
    if not callable(gradient):
        raise TypeError("'gradient' must be callable")

    # Setting up the data type for NumPy arrays
    dtype_ = np.dtype(dtype)

    # Converting x and y to NumPy arrays
    x, y = np.array(x, dtype=dtype_), np.array(y, dtype=dtype_)
    n_obs = x.shape[0]
    if n_obs != y.shape[0]:
        raise ValueError("'x' and 'y' lengths do not match")
    # Make matrix out of all x and y points, smash the matrices together columnwise
    # This makes shuffling easier later on by shuffling x and y simultaneously
    xy = np.c_[x.reshape(n_obs, -1), y.reshape(n_obs, 1)]

    # Initializing the random number generator
    seed = None if random_state is None else int(random_state)
    rng = np.random.default_rng(seed=seed)

    # Initializing the values of the variables
    vector = np.array(start, dtype=dtype_)

    # Setting up and checking the learning rate
    learn_rate = np.array(learn_rate, dtype=dtype_)
    if np.any(learn_rate <= 0):
        raise ValueError("'learn_rate' must be greater than zero")

    # Setting up and checking the size of minibatches
    batch_size = int(batch_size)
    print("batch_size:", batch_size)
    if not 0 < batch_size <= n_obs:
        raise ValueError(
            "'batch_size' must be greater than zero and less than "
            "or equal to the number of observations"
        )

    # Setting up and checking the maximal number of iterations
    n_iter = int(n_iter)
    if n_iter <= 0:
        raise ValueError("'n_tier' must be greater than zero")

    # Setting up and checking the tolerance
    tolerance = np.array(tolerance, dtype=dtype_)
    if np.any(tolerance <= 0):
        raise ValueError("'tolerance' must be greater than zero")

    # initialize plotting variables
    accuracy = []
    theoretical = []
    iter_num = []

    # deriving constants
    # lecture 18 page 16
    def terms_in_bound(learn_rate):
        # get eigenvalues, n, and all norms of the rows of x
        eig, _ = np.linalg.eig(np.matmul(x.T, x))
        n = x.shape[0]
        row_norm = [(np.linalg.norm(x[j, :])) ** 2 for j in range(rows)]

        # get sigma
        inp_diff = [np.abs((np.dot(x[j, :], ideal) - y[j])) ** 2 for j in range(n)]
        sigma2 = (
            n ** (1.4)
            * sum([row_norm[j] * inp_diff[j] for j in range(n)])
            / (batch_size**2)
        )[0]

        # get the constants L, mu, alpha etc
        mu = min(sorted(eig))
        L = n * max(row_norm)

        if learn_rate >= 1 / (L):
            alpha = 1 / (2 * L)

        else:
            alpha = learn_rate
        grad = gradient(x, y, ideal)

        print("alpha: ", alpha)
        print("L: ", L)
        print("mu: ", mu)
        print("sigma^2: ", sigma2)

        # terms in bound
        coeff = 1 - 2 * alpha * mu * (1 - alpha * L)
        norm = np.linalg.norm(start - ideal) ** 2
        frac = alpha * (sigma2) / (mu * (1 - alpha * L))
        print(f"alpha: {alpha}\nalpha/(mu(1 - alpha*L)): {frac/sigma2}")
        return coeff, norm, frac

    def theory_bound(i, coeff, norm, frac):
        return (coeff**i) * norm + frac

    # compute these terms once
    coeff, norm, frac = 0, 0, 0
    if plot_title:
        coeff, norm, frac = terms_in_bound(learn_rate=learn_rate)
        print(coeff, norm, frac)

    accuracy.append(np.linalg.norm(start - ideal) ** 2)
    theoretical.append(theory_bound(0, coeff, norm, frac))
    iter_num.append(0)
    # Performing the gradient descent loop
    for i in range(n_iter):
        # Shuffle x and y
        rng.shuffle(xy)

        # Performing minibatch moves
        for start in range(0, n_obs, batch_size):
            stop = start + batch_size
            x_batch, y_batch = xy[start:stop, :-1], xy[start:stop, -1:]

            # Recalculating the difference
            grad = np.array(gradient(x_batch, y_batch, vector), dtype_)
            diff = -learn_rate * grad
            # Checking if the absolute difference is small enough
            if np.all(np.linalg.norm(diff) <= tolerance):
                break

            # Updating the values of the variables
            vector += diff

        acc = np.linalg.norm(vector - ideal) ** 2
        # print(f"completed iteration {i}, ||pred - b|| = {acc}")
        if plot_title:
            iter_num.append(i + 1)
            accuracy.append(acc)
            theoretical.append(theory_bound(i * mul, coeff, norm, frac))

    if plot_title:
        import matplotlib.pyplot as plt

        plt.rcParams.update({"text.usetex": True, "font.family": "Helvetica"})
        plt.plot(iter_num, accuracy, c="b")
        plt.plot(iter_num, theoretical, c="r")
        plt.xlabel("Iteration Number")
        plt.ylabel(r"Criterion gap: $ \|w_t- w^*\|^2 $")
        plt.title(plot_title)
        plt.savefig(filename)
        plt.close()

    print("\n\nExperimental, Theoretical")
    print(
        accuracy[0],
        "&",
        accuracy[-1],
        "&",
        ((accuracy[0] - accuracy[-1]) / accuracy[0]) * 100,
        "&",
        theoretical[0],
        "&",
        theoretical[-1],
        "&",
        ((theoretical[0] - theoretical[-1]) / theoretical[0]) * 100,
    )
    print("\n")
    return vector if vector.shape else vector.item()


# the rows and columns of the matrices in this problem
rows = 10000
cols = 1000

# the various epsilons
ep1 = np.random.normal(0, 1, size=(rows, 1))
ep2 = np.random.normal(0, 0.1, size=(rows, 1))
ep3 = np.random.normal(0, 0.01, size=(rows, 1))
ep4 = np.random.normal(0, 0, size=(rows, 1))

# a cols x 1 column vector, correct shape to multiply with A
ones = np.ones(shape=(cols, 1))


def problem3a():
    mu = 0
    sigma = 1 / math.sqrt(cols)
    A = np.random.normal(mu, sigma, (rows, cols))

    # setup the b and w vectors
    M = np.matmul(np.linalg.inv(np.matmul(np.transpose(A), A)), np.transpose(A))
    b0 = np.matmul(A, ones)
    bs = [b0 + ep1, b0 + ep2, b0 + ep3, b0 + ep4]
    w_min = [np.matmul(M, b) for b in bs]
    w_0 = np.random.uniform(low=0, high=5, size=(cols, 1))

    # hyper-parameters
    stepsize = 0.1
    batch_size = 100
    num_iter = 100
    mul = 1000

    # graphing
    titles = [
        r"Fixed Var($A$), Var($\epsilon$) = 1",
        r"Fixed Var($A$), Var($\epsilon$) = 0.1",
        r"Fixed Var($A$), Var($\epsilon$) = 0.01",
        r"Fixed Var($A$), Var($\epsilon$) = 0",
    ]
    filenames = ["graph1.png", "graph2.png", "graph3.png", "graph4.png"]

    def grad_loss(X, y, w):
        """
        Gradient of the least squares loss function
        """
        return np.matmul(np.transpose(X), np.matmul(X, w) - y)

    def grad_loss_js(X, y, w):
        """
        Gradient of the least squares loss function for the jth part
        """
        AtA = np.matmul(X.transpose(), X)
        n = w.shape[0]
        stupid = [AtA[:, j].reshape((n, 1)) * w[j] for j in range(n)]
        Atb = np.matmul(X.transpose(), y)
        print(AtA)
        print(Atb)
        print()

        components = [stupid[j] + (Atb / n) for j in range(n)]
        return components

    for i in range(len(bs)):
        b = bs[i]
        w_best = w_min[i]
        title = titles[i]
        sgd(
            gradient=grad_loss,
            gradient_js=grad_loss_js,
            x=A,
            y=bs[i],
            start=w_0,
            learn_rate=stepsize,
            ideal=w_min[i],
            batch_size=batch_size,
            n_iter=num_iter,
            plot_title=titles[i],
            mul=mul,
            filename=filenames[i],
        )


def problem3b():
    mu = 0
    sigma = lambda j: 1 / math.sqrt(cols * j)
    A = np.array([np.random.normal(mu, sigma(j), (cols)) for j in range(1, rows + 1)])

    # setup the b and w vectors
    M = np.matmul(np.linalg.inv(np.matmul(np.transpose(A), A)), np.transpose(A))
    b0 = np.matmul(A, ones)
    bs = [b0 + ep1, b0 + ep2, b0 + ep3, b0 + ep4]
    w_min = [np.matmul(M, b) for b in bs]
    w_0 = np.random.uniform(0, 1, size=(cols, 1))

    # hyper-parameters
    stepsize = 0.1
    batch_size = 10
    num_iter = 1000
    mul = 1000

    # graphing
    titles = [
        r"Varying Var($A$), Var($\epsilon$) = 1",
        r"Varying Var($A$), Var($\epsilon$) = 0.1",
        r"Varying Var($A$), Var($\epsilon$) = 0.01",
        r"Varying Var($A$), Var($\epsilon$) = 0",
    ]
    filenames = ["graph5.png", "graph6.png", "graph7.png", "graph8.png"]

    def grad_loss(X, y, w):
        """
        Gradient of the least squares loss function
        """
        return np.matmul(np.transpose(X), np.matmul(X, w) - y)

    def grad_loss_js(X, y, w):
        """
        Gradient of the least squares loss function for the jth part
        """
        AtA = np.matmul(X.transpose(), X)
        n = w.shape[0]
        stupid = [AtA[:, j].reshape((n, 1)) * w[j] for j in range(n)]
        Atb = np.matmul(X.transpose(), y)
        print(AtA)
        print(Atb)
        print()

        components = [stupid[j] + (Atb / n) for j in range(n)]
        return components

    for i in range(len(bs)):
        b = bs[i]
        w_best = w_min[i]
        title = titles[i]
        sgd(
            gradient=grad_loss,
            gradient_js=grad_loss_js,
            x=A,
            y=bs[i],
            start=w_0,
            learn_rate=stepsize,
            ideal=w_min[i],
            batch_size=batch_size,
            n_iter=num_iter,
            plot_title=titles[i],
            mul=mul,
            filename=filenames[i],
        )


problem3b()
